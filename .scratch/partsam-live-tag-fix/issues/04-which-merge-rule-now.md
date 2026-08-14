# 04 - Which merge rule now

Type: grilling
Status: resolved
Blocked by: 01, 03

## Question

After the live ficus run erased tag 2, what merge rule should the spec state?

Candidates (not exhaustive): keep **highest chosen-mask predicted IoU** (smaller mask on ties); restore the trial’s **named order trunk > leaves > pot**; IoU but **trunk cannot lose to leaves** on overlap; something else that still uses names only as labels.

Do not retune for a thinner trunk as a success bar. Do not implement. This ticket **chooses** the rule the spec will write.

## Answer

Keep **highest chosen-mask predicted IoU** (names are labels; **smaller mask** on IoU ties). Add a generic **survival** constraint: after NN lift, every Stage 2 group that had a non-empty raw mask and at least one positive click must have a non-empty tag ID on the Material Tag Tensor.

If the IoU pass leaves a prompted ID empty, restore that group’s **full raw mask** on the 100k (overlap included) and lift again. If several prompted IDs are empty, restore in **increasing chosen IoU** (lowest first) so a later restore overwrites overlap — higher IoU still ranks. Skip a group whose raw mask was empty. At most one restore pass per prompted group.

Rejected: named order trunk > leaves > pot; “trunk cannot lose to leaves.”

