rm(list = ls())

library(tidyverse)

data <- tibble(
    learning_rate = rep(c(0.01, 0.05, 0.1), each = 3),
    ngram_size = rep(c("1", "2", "3"), times = 3),
    auc = c(0.9019483361008155, 0.8985675928328255, 0.7627563338905388,
            0.9036257241517349, 0.9044877488592841, 0.7693852143472046,
            0.9034636511888169, 0.9068863742837410, 0.7727091640831082))


data_matrix <- as.matrix(select(data, auc), ncols = 3, nrows = 3)

ggplot(data, aes(x = ngram_size, y = learning_rate)) +
    scale_x_discrete(
        "n-grams size",
        labels = c("1" = "mono-grams", "2" = "bi-grams", "3" = "tri-grams"),
        position = "top") +
    geom_point(aes(colour = - rank(auc), size = 100 * auc)) +
    geom_text(aes(y = learning_rate + 0.006,
                  label = paste0(round(100 * auc, 2), "%"))) +
    scale_colour_gradientn(colours = heat.colors(9)) +
    labs(color = "AUC") +
    theme(legend.position = "none") +
    ggtitle("Results of Grid Search") +
    ylab("Learning rate")


ggsave(filename = "binary_class_grid_search.png", device = "png",
       width = 5, height = 5)
