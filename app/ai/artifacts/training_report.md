# Model training report

Dataset: 8000 synthetic rows (seed 42)
Fraud rate: 0.0449

## risk model

- accuracy: 0.8965
- precision: 0.8820
- recall: 0.8321
- f1: 0.8530

### Confusion matrix

```
actual \ predicted                  HIGH                 LOW              MEDIUM
HIGH                                 138                   0                  62
LOW                                    0                1123                  51
MEDIUM                                18                  76                 532
```

### Top feature importances

- numeric__amount_to_available_ratio: 0.5092
- numeric__transaction_amount: 0.1729
- numeric__debit_transaction_blocked: 0.1260
- numeric__blocked_balance: 0.0590
- numeric__available_balance: 0.0479
- numeric__current_balance: 0.0325
- numeric__overdraft_limit: 0.0179
- numeric__is_primary_account: 0.0089
- categorical__transaction_type_WITHDRAW: 0.0026
- categorical__currency_TRY: 0.0026

## fraud model

- accuracy: 0.8965
- precision: 0.2632
- recall: 0.7222
- f1: 0.3858
- roc_auc: 0.8765

### Confusion matrix

```
actual \ predicted                     0                   1
0                                   1728                 182
1                                     25                  65
```

### Top feature importances

- numeric__amount_to_available_ratio: 0.2675
- numeric__debit_transaction_blocked: 0.2670
- numeric__transaction_amount: 0.1459
- numeric__available_balance: 0.0620
- numeric__current_balance: 0.0572
- categorical__transaction_type_TRANSFER: 0.0333
- numeric__overdraft_limit: 0.0311
- categorical__currency_TRY: 0.0238
- numeric__blocked_balance: 0.0194
- numeric__is_primary_account: 0.0114
