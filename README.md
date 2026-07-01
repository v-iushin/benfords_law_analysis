# Benford's Law Across Real Datasets

A statistical investigation of when and why real-world data follows Benford's Law, based on four datasets: country GDP, country population, country land area, and city population.



## Overview

Benford's Law, also known as the First-Digit Law, is the empirical observation that in many real-life numerical datasets, the leading (first) digit distribution is non-uniform and follows:

Benford's Law, also known as the First-Digit Law, is the empirical observation that in many real-life numerical datasets, the distribution of the leading (first) digit is non-uniform, with digit probabilities given by:

$$
P(d) = \log_{10}\left(1 + \frac{1}{d}\right), \quad d = 1, \dots, 9
$$

This means the leading digit 1 occurs about 30% of the time, while the digit 9 occurs only about 5% of the time. The law is used in fraud detection because fabricated numbers tend not to follow this pattern.

This small project doesn't just check whether a dataset passes or fails; it investigates why and when it does. The main finding is that whether data follows Benford's Law depends on two independent properties of the dataset:

1. How many orders of magnitude the dataset spans across, measured as $\sigma$ (sigma), the standart deviation of $\log_{10}$ of the values.
2. Whether the individual observations are statistically independent; $\chi^2$-test can be distorted by correlated data.
