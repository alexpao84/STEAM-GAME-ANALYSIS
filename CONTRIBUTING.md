# Contributing to Steam Playtime Analysis

Thanks for your interest in contributing to Steam Playtime Analysis.
This project aims to provide a transparent, reproducible and honest analysis of Steam game engagement using public data and explicit assumptions.

We value clarity over complexity and consistency over speculative precision.

## Guiding principles

Before contributing, please keep in mind:

- This project does not aim to produce exact telemetry
- All metrics are explicit estimates
- Every assumption must be documented and reproducible
- Simplicity and readability matter more than clever tricks

If your contribution makes the project harder to understand, it’s probably not a good fit.

## What you can contribute

We welcome contributions in the following areas:

### Data & methodology

- Improved playtime estimation models
- Retention or decay curves
- Aging analysis (years since release)
- Normalization of genres and tags

### Analysis & validation

- Cross-validation with external datasets
- Sensitivity analysis on assumptions
- Bias and limitation analysis

### Visualization

- Dashboards (Power BI, Streamlit, Tableau)
- Clear and reproducible charts
- Data storytelling notebooks

### Code quality

- Refactoring for readability
- Performance improvements
- Better error handling and logging

# What we will not accept

To keep the project focused, we do not accept:

- Black-box models without explanation
- Claims of “real user behavior” or demographics
- Scraping that violates Steam’s ToS
- Over-engineering or unnecessary dependencies
- Large raw datasets committed to the repository

# How to contribute
## 1. Fork the repository

Create a fork and work on your branch.

## 2. Create a descriptive branch name

Examples:

feature/genre-normalization
analysis/retention-model
docs/methodology-clarification

## 3. Keep changes focused

One contribution per pull request.
Small, reviewable PRs are preferred.

## 4. Document assumptions

If you change:

- formulas
- constants
- aggregation logic

**explain why in comments or documentation.**

# Testing your changes

Before submitting a PR:

- Run the analysis script end-to-end
- Ensure outputs are generated without errors
- Avoid hard-coding paths or environment-specific settings

If you add new logic, include:

- inline comments
- or a short explanation in the PR description

# Data handling rules

- Raw datasets go in data/raw/ (ignored by git)
- Processed outputs go in data/processed/ (ignored by git)

If needed, include small sample files only for demonstration

**Never commit:**

- large CSVs
- scraped dumps
- proprietary or private data

# Licensing

By contributing, you agree that your contributions will be released under the MIT License, consistent with the rest of the project.

# Code of conduct

Be respectful and constructive.
This is a technical project — debate ideas, not people.

# Final note

This repository is intentionally opinionated:

- transparent assumptions
- reproducible logic
- analytical honesty

If that aligns with how you think about data, you’re very welcome here.

Happy contributing