# Interrupted integrated service check — diagnostic only

The full service checker was stopped after the 26 September 2026 CAD freeze was revoked. It did not produce a completed report and is not verification authority.

- Motion source: `9f3fe8214a58285249a1ac7313e5f39b7658349eb3a4f6a259faeb162e953def`.
- Service source: `9738b260ce8f61c7ca45b46c212b1559057bdb1b1505885bcc0616045bc228e5`.
- Checker: `c2f0cc1c5750d7c7514d19fb77eab48ce52932edfa40acf466cf9274a646fdde`.
- Console results: router 1,669 parts / 1 unresolved intersection; stored 1,669 / 1; tail parked 1,657 / 1; hatches open 1,657 / 1.
- The simultaneous root static report identified `I_HEAD_CAP_1_103_17` against `I_PARK_BOLT_2`, overlap 0.71691 mm³. This is a motion/parking defect; it was not accepted or excluded.

Service routes were not completed in this interrupted run. A later complete passing run against the corrected shared sources must replace it as current authority. No service CAD or checker source was changed during this run.
