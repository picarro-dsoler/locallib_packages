# locallib.analytics

A local analytics library containing representative emission rate calculations.

## Installation

Install in development mode:

```bash
pip install -e .
```

## Usage

```python
from locallib.analytics import BinnedRER

# Create an instance of the BinnedRER class
rer = BinnedRER()

# Set experimental data
experiments = [0.5, 1.2, 0.8, 2.1, 0.3]  # Example data
rer.set_experiments(experiments)

# Get actual leak distribution
actual_dist = rer.get_actual_leak_distribution()
print(actual_dist)

# Get posterior probability matrix
posterior_prob = rer.get_posterior_probability_matrix()
print(posterior_prob)

# Get posterior leak distribution
posterior_dist = rer.get_posterior_leak_distribution()
print(posterior_dist)
```

## Classes

### BinnedRER

A class for calculating representative emission rates using binned data and Bayesian analysis.

#### Methods

- `set_experiments(experiments)`: Set experimental data and calculate actual leak distribution
- `set_actual_leak_distribution(actual_leak_distribution=None)`: Set or calculate the actual leak distribution
- `get_actual_leak_distribution()`: Get the actual leak distribution
- `get_posterior_probability_matrix()`: Calculate and return the posterior probability matrix
- `get_posterior_leak_distribution()`: Calculate and return the posterior leak distribution

## Requirements

- pandas >= 1.0.0
- numpy >= 1.18.0