# aws-stack-set-snapshot

Dumps all instances of all stack sets.

This allows you to compute statistics across all stack instances, such as total instance count and ratio of CURRENT instances.

## Quick Start

Count the instances in each stack set.

```bash
poetry run python aws_stack_set_snapshot.py > stack_sets.json

cat stack_sets.json \
| jq 'map({StackSetName, Instances: (.Instances | length)})' \
| in2csv --format json \
| csvlook \
| less
```

## Implementation

Returns the Summaries list of ListStackSets and adds an Instance key. The Instance key is populated by the Summaries list of ListStackInstances for each stack set.
