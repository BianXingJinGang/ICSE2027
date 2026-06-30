# PatchCourt Qualitative Case Studies 2026-05-28

These cases are drafted for paper prose. They are not additional samples; they explain the mechanics behind the quantitative tables. Each case should be linked to a certificate or table row in the final artifact.

## Case A: Seaborn MultiIndex Pairplot, Cross-Source Agreement On The Failure Mode

Task: `mwaskom__seaborn-3407`

Probe: `upgrade-fullpkg-seaborn-pairplot-multiindex`

Why this is the strongest case:

- It appears in the main upgraded probe layer.
- It is also the only Qwen issue/full-package pass/fail BDC after multi-sample generation.
- The probe executes Seaborn package behavior rather than an isolated helper.
- The public issue signal is concrete: `pairplot` must handle a dataframe with MultiIndex-like columns without failing on column access.

Observed behavior:

- In the original upgraded layer, visible-passing candidates split under the full-package pairplot reproducer.
- In the Qwen multi-sample layer, 1 of 5 Qwen/no-op visible-pass candidates passes the reproducer and 4 fail.
- The passing Qwen sample prints the expected axes shape; the failing groups include import failures and pairplot indexing failures.

Certificate evidence chain:

- Main certificate: `mwaskom__seaborn-3407::upgrade-fullpkg-seaborn-pairplot-multiindex::c360f3811a8c`.
- Main behavior: `3` pass, `1` fail, `0` timeout; pass group prints `axes_shape (4, 4)` and fail group raises through the Seaborn `pairplot`/axis-grid path.
- Qwen certificate: `mwaskom__seaborn-3407::upgrade-fullpkg-seaborn-pairplot-multiindex::c0e48032bf03`.
- Qwen behavior: `1` pass, `4` fail, `0` timeout; pass group again prints `axes_shape (4, 4)`.
- Why this is not an oracle: the certificates show executable disagreement among visible-pass hypotheses; they do not prove the passing candidate is the unique correct repair.

Paper prose:

"The Seaborn MultiIndex case illustrates why PatchCourt treats visible-passing patches as competing executable hypotheses. The visible layer admits several Qwen structured edits, but the issue-level package probe separates them sharply: one sample drives `pairplot` to completion, while the remaining samples fail through import or dataframe-indexing paths. The certificate does not require the developer patch, but it gives an auditable reason to abstain from accepting the visible-pass pool as equivalent."

Claim supported:

- Strong issue-specific Qwen BDC.
- Good first case study for RQ3/RQ4.

Boundary:

- This is one task. It cannot support a broad statement that Qwen reproduces all issue-specific BDCs.

## Case B: Matplotlib All-NaN Bar Plot, Full-Package Probe And Held-Out Failure

Task: `matplotlib__matplotlib-24149`

Probe: `upgrade-fullpkg-matplotlib-bar-all-nan`

Why this case matters:

- The held-out label is false acceptance: the visible/probe-accepted candidate fails FAIL_TO_PASS after freeze.
- The upgraded full-package probe also yields a pass/fail BDC.
- The issue is a compact numerical edge case, which is easy to explain in an ICSE paper.

Observed behavior:

- Visible tests accept candidates that differ on all-NaN bar dimensions.
- The package-level probe exercises Matplotlib axes behavior after the routed extension/build layer is available.
- Candidate behavior separates cleanly into pass and fail outcomes.

Certificate evidence chain:

- Certificate: `matplotlib__matplotlib-24149::upgrade-fullpkg-matplotlib-bar-all-nan::6d71aa269334`.
- Behavior: `3` pass, `1` fail, `0` timeout.
- Passing behavior prints `bar_count 1` and `bar_x nan`; the failing behavior exits through the Matplotlib axes stack.
- Held-out row: the frozen held-out table marks this task as false acceptance.
- Why this is not an oracle: the certificate is pre-freeze risk evidence; the false-acceptance label comes only from later held-out calibration.

Paper prose:

"The Matplotlib case shows the gap between repository-level visible tests and boundary-condition semantics. A candidate can satisfy the visible command set while mishandling an all-NaN plotting edge case. The upgraded probe executes the plotting stack rather than a source-isolated surrogate, and the post-freeze held-out run confirms that the accepted candidate is a false acceptance."

Claim supported:

- RQ1 false acceptance.
- RQ3 full-package upgrade survival.

Boundary:

- This case is not an independent Qwen-source result.

## Case C: Scikit-Learn LabelEncoder Empty Transform, From Build Routing To Integrity Boundary

Task: `scikit-learn__scikit-learn-10508`

Probes:

- Main issue probe: `upgrade-fullpkg-sklearn-labelencoder-empty-transform`
- Qwen integrity probe: `upgrade-fullpkg-integrity-sklearn-preprocessing-import`

Why this case matters:

- The main lane shows a full-package issue-level BDC after the compiled-extension/build-routing blocker is resolved.
- The Qwen lane does not produce a positive issue-specific pass/fail BDC, but it does produce a package-integrity pass/fail split.
- It is a clean example of why the paper must separate issue correctness from package integrity.

Observed behavior:

- Main upgraded probes split visible-passing candidates on the empty-transform API contract.
- Qwen issue/full-package samples all fail the semantic empty-transform assertion, so they are downgraded.
- Qwen package-integrity samples split on whether `sklearn.preprocessing.LabelEncoder` can be imported and constructed.

Certificate evidence chain:

- Main issue certificate: `scikit-learn__scikit-learn-10508::upgrade-fullpkg-sklearn-labelencoder-empty-transform::40b7bfac5420`.
- Main behavior: `3` pass, `1` fail, `0` timeout; pass group prints `empty_shape (0,)` and `empty_size 0`, while the fail group hits a NumPy casting path.
- Qwen issue certificate: `scikit-learn__scikit-learn-10508::upgrade-fullpkg-sklearn-labelencoder-empty-transform::1226863ffd7a`.
- Qwen issue behavior: `0` pass, `5` fail, `0` timeout; downgraded for issue-specific claims.
- Qwen integrity certificate: `scikit-learn__scikit-learn-10508::upgrade-fullpkg-integrity-sklearn-preprocessing-import::281b7e4dd110`.
- Qwen integrity behavior: `2` pass, `3` fail, `0` timeout; pass group prints `label_encoder LabelEncoder`.
- Why this is not an oracle: the integrity split diagnoses package damage or preservation, not whether the issue itself is fixed.

Paper prose:

"The Scikit-Learn case is useful precisely because it prevents an overclaim. In the main lane, the LabelEncoder empty-transform reproducer yields a pass/fail certificate once build routing is repaired. In the Qwen lane, however, the issue-specific reproducer remains all-fail; only a separate package-integrity check produces a pass/fail split. PatchCourt therefore records both facts but assigns them different evidentiary weights."

Claim supported:

- RQ3 upgrade evidence in the main lane.
- RQ4 package-integrity partial positive.

Boundary:

- Do not count the Qwen issue/full-package result as issue-specific success.

## Case D: Flask Routes Command, Package Damage Under Visible-Pass Qwen Samples

Task: `pallets__flask-5063`

Probes:

- Issue/full-package probe: `upgrade-fullpkg-flask-routes-subdomain-column`
- Integrity probe: `upgrade-fullpkg-integrity-flask-import-core`

Why this case matters:

- It is a strong example of a visible-pass Qwen patch pool containing package-breaking patches.
- It also shows why all-fail issue/full-package divergence must be downgraded.

Observed behavior:

- The issue/full-package route-command reproducer fails for all Qwen/no-op groups, though failure modes differ.
- The package-integrity probe splits candidates: some can import Flask and construct an app, while others fail import or core initialization.

Paper prose:

"The Flask case shows a second kind of independent-source risk. The route-command issue probe does not identify a passing Qwen candidate, so it is not a positive issue certificate. Yet the integrity probe reveals a visible-pass pool split between candidates that preserve core Flask import/app construction and candidates that break package initialization. This is exactly the distinction the audit layer is designed to preserve."

Claim supported:

- Independent-source package-integrity BDC.

Boundary:

- Not issue-specific Qwen success.

## Case E: Django Template Join Autoescape, Full-Package Semantic Probe Without Held-Out Failure

Task: `django__django-16873`

Probe: `upgrade-fullpkg-django-join-autoescape-off`

Why this case matters:

- It is a full-package upgraded BDC but not a held-out false acceptance.
- It shows that PatchCourt evidence is risk evidence, not a guaranteed hidden-test failure label.

Observed behavior:

- Visible-passing candidates disagree on template rendering semantics under `autoescape off`.
- The held-out label for the selected candidate is not false acceptance.

Certificate evidence chain:

- Certificate: `django__django-16873::upgrade-fullpkg-django-join-autoescape-off::3f215078cc87`.
- Behavior: `3` pass, `1` fail, `0` timeout.
- Passing behavior prints `<p>Hello World!</p><br/>beta & me<br/><script>Hi!</script>`; the failing behavior escapes the `<br/>` separators and raises an assertion.
- Held-out row: the frozen held-out table does not mark this selected candidate as false acceptance.
- Why this is not an oracle: BDCs flag unresolved behavioral disagreement and review risk; they are not hidden-test labels.

Paper prose:

"The Django join case is important because it is not a simple success story. PatchCourt detects a semantic split under full-package template rendering, but the selected candidate does not fail the held-out FAIL_TO_PASS labels. This is a useful validity check: BDCs are not hidden-test labels. They identify unresolved behavioral disagreement that can guide review, reranking, or abstention."

Claim supported:

- RQ3 probe upgrade.
- Threats/construct validity: BDC is a risk signal, not correctness oracle.

Boundary:

- Do not present every BDC as a held-out false acceptance.

## Case F: SymPy Empty Array, Issue-Code Probe As Middle Layer

Task: `sympy__sympy-23117`

Probe: `upgrade-issuecode-sympy-empty-array`

Why this case matters:

- It demonstrates the middle layer between source-isolated templates and full-package behavioral probes.
- The issue-code probe is compact and directly tied to a public reproducer.

Observed behavior:

- The upgraded issue-code probe yields a pass/fail BDC.
- The held-out label is not false acceptance, again reinforcing the risk-signal framing.

Certificate evidence chain:

- Certificate: `sympy__sympy-23117::upgrade-issuecode-sympy-empty-array::659ab52dbadd`.
- Behavior: `3` pass, `1` fail, `0` timeout.
- Passing behavior prints `array []` and `shape (0,)`; the failing behavior raises through the candidate SymPy repo.
- Why this is not an oracle: the issue-code snippet is a compact public reproducer and should be read as stronger-than-template evidence, not as final correctness ground truth.

Paper prose:

"The SymPy case motivates the issue-code layer. Some public reports contain compact executable snippets that can be run directly against candidate worktrees. PatchCourt treats these snippets as stronger than source-isolated templates but still below post-freeze held-out labels. The resulting certificate is auditable and cheap, yet the paper keeps it separate from correctness ground truth."

Claim supported:

- RQ3 layered probe design.
- Artifact interpretability.

Boundary:

- Not an independent-source Qwen result.

## Recommended Case Study Placement

Main text:

1. Seaborn MultiIndex pairplot as the opening motivating certificate.
2. Matplotlib all-NaN bar plot as the held-out false-acceptance example.
3. Scikit-Learn LabelEncoder as the audit-boundary example.
4. Django or SymPy as the "risk signal, not oracle" example.

Appendix:

- Flask route command as Qwen package-integrity example.
- Full table of retained, downgraded, and rejected Qwen certificates.
