# IBM Quantum Setup

Simulator-first work requires no IBM credentials. Install optional packages only when needed:

```bash
python -m pip install -e ".[quantum,ibm]"
```

Store IBM account details using IBM's supported secure account storage or environment variables outside Git. Never commit tokens. Hardware execution must be explicit, show circuit resources and shots first, and require a confirmation flag before submission.
