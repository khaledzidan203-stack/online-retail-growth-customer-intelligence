# Data quality

Canonical processing preserves rows with classification, eligibility, customer-identity, price and duplicate indicators. See [classification precedence](data_quality/TRANSACTION_CLASSIFICATION.md) and [baseline](data_quality/DQ_BASELINE.md).

Eligible merchandise drives sales and units. Customer cancellations remain separate and use absolute values. Operational stock adjustments are quantity events with zero monetary value; accounting adjustments stay separate. Anonymous activity can be valid sales. Duplicate exposure is reported without silently removing rows.

Flags describe governance or review exposure, not automatic invalidity. The observation period has partial years at both ends; cancellation rates for small markets are volatile.
