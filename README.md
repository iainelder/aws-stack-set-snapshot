# aws-stack-set-snapshot

Dumps all instances of all stack sets.

This allows you to compute statistics across all stack instances, such as total instance count and ratio of CURRENT instances.

## Quick Start

Run the tool in the organization management account.

Dump a snapshot.

```bash
poetry run python aws_stack_set_snapshot.py > stack_sets.json
```

Count the instances in each stack set.

```bash
cat stack_sets.json \
| jq 'map({StackSetName, Status, Instances: (.Instances | length)})' \
| in2csv --no-inference --format json \
| csvlook --no-inference \
| less
```

Columns:

* StackSetName
* Status
* Instances

Show the result of the latest operation.

```bash
cat stack_sets.json \
| jq '
map({
    StackSetName,
    Status,
    LastOperation: (
        .Operations[0]
        | if . == null then {}
          else {Status, CreationTimestamp, EndTimestamp} end)
})
| sort_by(.LastOperation.CreationTimestamp)
| reverse
' \
| in2csv --no-inference --format json \
| csvlook --no-inference \
| less
```

Columns:

* StackSetName
* Status
* LastOperation/Status
* LastOperation/CreationTimestamp
* LastOperation/EndTimestamp

Compute the aggregate status of all the instances.

```bash
cat stack_sets.json \
| jq '
map(select(.Status == "ACTIVE"))
| map(
    {StackSetName}
    + (
        .Instances
        | reduce .[] as $i (
            {
                "CURRENT_RATIO": 0,
                "TOTAL": 0,
                "CURRENT_SUCCEEDED": 0
            }
            ; .[$i.Status + "_" + $i.StackInstanceStatus.DetailedStatus] += 1
            | .["TOTAL"] += 1
            | .["CURRENT_RATIO"] = (100 * .["CURRENT_SUCCEEDED"] / .["TOTAL"] | floor)
        )
    )
)
| sort_by(.CURRENT_RATIO, .StackSetName)
' \
| in2csv --no-inference --format json \
| csvlook --no-inference \
| less
```

Columns:

* StackSetName
* CURRENT_RATIO
* TOTAL
* CURRENT_SUCCEEDED
* OUTDATED_FAILED
* OUTDATED_CANCELLED
* INOPERABLE_INOPERABLE
* OUTDATED_PENDING

Show the target regions and organizational units.

```bash
cat stack_sets.json \
| jq '
map(select(.Status == "ACTIVE"))
| map(
    {StackSetName}
    + (
        .Instances
        | reduce .[] as $i (
            {
                "Regions": {},
                "OrganizationalUnitIds": {}
            }
            ; .Regions[$i.Region] += 1
            | .OrganizationalUnitIds[$i.OrganizationalUnitId] += 1
        )
        | .Regions = (.Regions | keys | join(","))
        | .OrganizationalUnitIds = (.OrganizationalUnitIds | keys | join(","))
    )
)
' \
| in2csv --no-inference --format json \
| csvlook --no-inference \
| less
```

Columns:

* StackSetName
* Regions
* OrganizationalUnitIds

## TODO

jq lacks date arithmetic, so it's difficult to compute these:

* Days since last operation
* Duration of last operation
* Numer of operations per day (SERVICE_MANAGED stack sets operate automatically)

The SERVICE_MANAGED permission model is not supported in delegated administrator accounts. The tool is hard-coded to use the SELF permission model, so it currently works only in the organization management account.

Transform the JSON into a dimensional model with these dimensions (not exhaustive):

* Region
* Account (rolls up to Organizational unit, root, organization)
* Stack set 
* Status reason (with a pattern to match examples in the wild)

## Implementation

Returns the Summaries list of ListStackSets and adds extra keys to each stack set description.

Merges the complete description into each summary result given by DescribeStackSet.

The Instance key is populated for each stack set by the Summaries list of ListStackInstances.

The Operations key is populated for each stack set by the Summaries list of the ListStackSetOperations.

## Other Tools

[rain](https://github.com/aws-cloudformation/rain) now has a `stackset` command for operating on stack sets. I haven't tried it yet, but it may complement this tool.
