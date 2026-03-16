library(tidyverse)
library(lme4)

## Set plotting preferences
ggplot2::theme_set(ggplot2::theme_bw(base_size=18))
ggplot2::theme_update(panel.grid = ggplot2::element_blank(), 
                      strip.background = ggplot2::element_blank(),
                      legend.key = ggplot2::element_blank(),
                      panel.border = ggplot2::element_blank(),
                      axis.line = ggplot2::element_line(),
                      strip.text = ggplot2::element_text(face = "bold"),
                      plot.title = element_text(hjust = 0.5))
options(ggplot2.discrete.colour = c("#A31F34", "#8A8B8C"))
options(ggplot2.discrete.fill = c("#A31F34", "#8A8B8C"))

## Set working directory
setwd(dirname(rstudioapi::getActiveDocumentContext()$`path`))

dat <- read_csv("data.csv")

str(dat)

table(dat$correct)

table(dat$rank)

table(dat$condition)

table(dat$condition, dat$rank)

table(dat$subject_id)
length(unique(dat$subject_id))

table(dat$item_id)
length(unique(dat$item_id))

table(dat$word)
table(dat$word) %>% table

length(unique(dat$word))

dat$word[1]

dat$condition <- as.factor(dat$condition)
contrasts(dat$condition)

zipfian_only <- dat %>% 
  filter(
    condition == "zipfian"
  ) %>%
  group_by(subject_id, rank) %>%
  summarize(
    prop_correct = mean(correct)
  ) %>%
  group_by(rank) %>%
  summarize(
    std_error = sd(prop_correct) / sqrt(n()),
    prop_correct = mean(prop_correct)
  )

zipfian_only_by_participant <- dat %>% 
  filter(
    condition == "zipfian"
  ) %>%
  group_by(subject_id, rank) %>%
  summarize(
    prop_correct = mean(correct)
  )

ggplot(zipfian_only) +
  geom_line(aes(x = rank, y = prop_correct)) +
  geom_point(aes(x = rank, y = prop_correct)) +
  geom_point(
    data = zipfian_only_by_participant,
    aes(x = rank, y = prop_correct, group = subject_id),
    color = "gray",
    alpha = 0.5,
    position=position_jitter(width = 0.1, height = .05)
  ) + 
  geom_errorbar(aes(x = rank, ymin = prop_correct - std_error, ymax = prop_correct + std_error), width = 0.2) +
  labs(x = "Rank", y = "Proportion Correct", title = "Zipfian Condition Only")

dat <- dat %>%
  mutate(
    rank = ifelse(
      condition == "zipfian",
      rank - 1,
      rank
    )
  )

dat$condition <- relevel(dat$condition, ref="zipfian")


## Basic linear model
lm(
  correct ~ condition + rank,
  dat
)

## We have dependent observations
table(dat$word)
table(dat$foil)

table(table(dat$item_id))
table(table(dat$foil))
table(table(dat$word))


table(dat$word, dat$foil, dat$item_id)


lmer(
  correct ~ condition + rank + (rank | subject_id) + (condition + rank | word / foil),
  dat 
)

fit_logistic <- glmer(
  correct ~ condition + rank + (rank | subject_id) + (condition + rank | word / foil),
  dat,
  family = binomial,
  control = glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5))
)

fit_logistic

logit2prob <- function(logit) {
  odds <- exp(logit)
  prob <- odds / (1 + odds)
  return(prob)
}

## Intercept in probabilities (this is uniform rank 0)
logit2prob(0.90624)
## Zipfian in probabilities
logit2prob(0.90624 + 0.64128)
## Zipfian at rank =1 (assuming we start at 0)
logit2prob(0.90624 - 0.33425)
## Zipfian at rank =2 (assuming we start at 0)
logit2prob(0.90624 - 2*0.33425)
## Zipfian at rank =3 (assuming we start at 0)
logit2prob(0.90624 - 3*0.33425)

## Plot the model
library(sjPlot)
plot_model(fit_logistic, type="pred")[1]
plot_model(fit_logistic, type="pred")[2]

## Summary function on model output
summary(fit_logistic)

## Estimated marginal means by rank
library(emmeans)
summary(emmeans(fit_logistic, ~ condition | rank, at = list(rank = 0:3)), null = 0)

## Estimated marginal means overall
summary(emmeans(fit_logistic, ~ condition, at = list(condition = "zipfian")))
logit2prob(1.548)
logit2prob(1.213)
logit2prob(0.879)
logit2prob(0.545)
