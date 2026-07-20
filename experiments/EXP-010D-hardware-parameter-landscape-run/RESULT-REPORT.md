# EXP-010D-R3 hardware parameter-landscape result

One governed 32-PUB SamplerV2 job ran on `ibm_fez`, with 4,096 shots per PUB. All PUBs were
present, correctly ordered, and decoded into the frozen q0..q3 convention. No retry, backend
substitution, layout substitution, mitigation, postselection, or result exclusion occurred.

## Primary result

- Spearman rho across the 25 unique cells: `0.96`
- One-sided permutation p-value (100,000 permutations, seed 20260720):
  `0.00000999990000099999`
- Paired-cell bootstrap 95% interval (10,000 resamples):
  `[0.8670835382646556, 0.9891640866873065]`
- Frozen classification: **LANDSCAPE SUPPORTED**

The result supports preservation of the frozen local parameter-landscape ordering in this one
small controlled hardware run. It is not evidence of quantum advantage, speedup, generalisation,
or commercial usefulness. Exact classical evaluation remains authoritative.

## Secondary results and warnings

- Best hardware cell: centre `g+0_b+0`, R `0.5184178203750598`
- Centre rank: `1`; aggregate P(`1010`): `0.2357177734375`
- Aggregate centre most-likely state: `1010`
- Centre-to-outer-ring median R gap: `0.12789086911449876`
- Centre mean R: `0.5184178203750598`; sample SD: `0.005613960473859979`
- Control mean R: `-0.06980593169147745`; sample SD: `0.0038474813672902137`
- Aggregate centre-minus-control bootstrap 95% interval:
  `[0.5828979751046811, 0.5941771214747746]`
- Repeatability warning: `false`
- Control-quality warning: `true`

The control warning is retained exactly as predeclared because `abs(mean control R) > 0.05`.
It does not permit exclusion, replacement, rerunning, or reinterpretation of any PUB.

## Provenance

- Governed source SHA: `e60e37d671e17465105ca471fedff8cef5e72e8e`
- Backend: `ibm_fez`
- Job ID: `d9es7cineu4c739oqv0g`
- Submission timestamp: `2026-07-20T06:44:02.140613Z`
- ISA QPY SHA-256: `8f9256b18c10dbe54f7d800a2a244b7656abfa66b7d2da698881147c0c0b79ab`
- Canonical workload SHA-256: `27e383f463e46207818e9ed2cd6111d59f43ee0b3552cc4046712a87602d9513`
- Intent SHA-256: `bb8e20deb179f84318cb2e6f9d7c74361f9ec616d9a9467375b8e73f9f53d747`
- Receipt SHA-256: `faddae5e859b082354a8cc77a3507f2feb2dabac1cdc46c6b3ed3dfc3d31943f`
