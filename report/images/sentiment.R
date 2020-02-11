library(tidyverse)
    

data <- tibble(
    stars = c("1", "2", "3", "4", "5"),
    sentiment = c(-0.0161, 0.0772, 0.1895, 0.2772, 0.3350))

ggplot(data, aes(x = stars, y = sentiment)) +
    scale_x_discrete(
        "Rate",
        labels = c("1" = "1 star", "2" = "2 stars", "3" = "3 stars", "4" = "4 stars", "5" = "5 stars"),,
        position = "top") +
    geom_bar(stat = "identity", aes(fill = sentiment)) +
    theme_minimal() +
    theme(legend.position = "none") +
    # ggtitle("Average sentiment score per rate") +
    ylab("Average sentiment")

ggsave(filename = "sentiment.png", device = "png",
       width = 5, height = 5)
