# script for running non-linear growth models for COVID-19 vaccination 
# at US county level

library(tidyverse)
library(dataverse)
library(brms)
library(cmdstanr)

# retrieve archived data at https://doi.org/10.7910/DVN/BFRIKI
county_vacc <- get_dataframe_by_name(filename='COVID_county_vacc_data.tab',
                                     dataset='10.7910/DVN/BFRIKI',
                                     server='dataverse.harvard.edu') %>%
  # some states have very few counties so we group them with neighboring states
  # and fit models on that group to help with the random effects
  mutate(STATE_GRP=ifelse(STATE_NAME=='DE'|STATE_NAME=='MD', 'DE_MD', STATE_NAME)) %>%
  mutate(STATE_GRP=ifelse(STATE_NAME=='RI'|STATE_NAME=='MA', 'RI_MA', STATE_GRP)) %>%
  mutate(STATE_GRP=ifelse(STATE_NAME=='DC'|STATE_NAME=='VA', 'DC_VA', STATE_GRP))


# logistic growth model formula with full random effects
# according to notation in Supplement:
# Asym = alpha
# rate = beta
# xmid = gamma

# some states give divergent transitions warnings so we refit them with larger
# adapt_delta values (e.g., 0.99) and this resolves the issue
model <- bf(CASES~Asym/(1+exp(-rate*(WEEK-xmid))),
            xmid~1|COUNTY,
            rate~1|COUNTY,
            Asym~1|COUNTY,
            nl=TRUE)

# run county-level models by state group
state_index <- 1
for (state in unique(county_vacc$STATE_GRP)) {
  df <- county_vacc %>% filter(STATE_GRP==state)
  # progress message
  print(paste0('Started with ', '(', state_index, ')', ': ', state))
  # fit model
  fit <- brm(model,
             data = df %>% filter(WEEK<=25) %>% mutate(WEEK=WEEK/max(WEEK)), # fit up to week 25 and scale
             family = brmsfamily("normal", "identity"),
             prior = c(prior(normal(0.5, 0.2), class = 'b', nlpar = 'Asym', coef = 'Intercept'),
                       prior(normal(10, 3), nlpar = 'rate', lb = 0), # shortcut for same prior on all popn-level effects of rate
                       prior(beta(2, 2), nlpar = 'xmid', lb = 0, ub = 1),
                       prior(exponential(5), class = 'sd', nlpar = 'Asym'), # Asym group-level random effect sd
                       prior(exponential(15), class = 'sd', nlpar = 'xmid'), # xmid group-level random effect sd
                       prior(exponential(15), class = 'sigma')),
             seed = 1234,
             iter = 10000, # 5000 warmup & 5000 sampling
             control = list(adapt_delta=0.9),
             cores = 4,
             backend = 'cmdstanr')

  print(paste0('Finished with: ', state))
  state_index <- state_index + 1
}
