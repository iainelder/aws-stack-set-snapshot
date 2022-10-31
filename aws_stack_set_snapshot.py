import boto3
import botocore.config
import json
import sys
import concurrent.futures as fut
import logging
import datetime
from typing import Any, Dict, Literal, List
from mypy_boto3_cloudformation import CloudFormationClient
from mypy_boto3_cloudformation.type_defs import (
    StackSetSummaryTypeDef,
    StackInstanceSummaryTypeDef,
    StackSetOperationSummaryTypeDef,
    StackSetTypeDef,
)

# TODO make this work for logdecorator
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

class StackSet(StackSetTypeDef):
    Instances: List[StackInstanceSummaryTypeDef]
    Operations: List[StackSetOperationSummaryTypeDef]


def main() -> None:
    session = boto3.Session()
    cfn = configure_client(session)
    
    stack_sets: List[StackSetSummaryTypeDef] = cfn.list_stack_sets()["Summaries"]

    with fut.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_stack_set = {
            executor.submit(f, cfn, s): s
            for s in stack_sets
            for f in (list_instances, list_operations, describe_stack_set)
        }
    
    for f in fut.as_completed(future_to_stack_set):
        stack_set = future_to_stack_set[f]
        stack_set.update(f.result())  # type: ignore[typeddict-item]
    
    dump_snapshot_to_json(stack_sets)


def configure_client(session: boto3.Session) -> CloudFormationClient:

    class RetryFilter(logging.Filter):

        def filter(self, record: logging.LogRecord) -> bool:
            if record.msg == "No retry needed.":
                return False
            return True

    boto3.set_stream_logger("botocore.retryhandler", logging.DEBUG)
    logging.getLogger("botocore.retryhandler").addFilter(RetryFilter())

    config = botocore.config.Config(
        retries = {
            "max_attempts": 10,
            "mode": "legacy"
        }
    )

    return session.client("cloudformation", config=config)

# @ld.log_on_start(
#     logging.INFO,
#     message="""Instances for stack set {stack_set["StackSetName"]}""",
#     logger=logger)
def list_instances(cfn: CloudFormationClient, stack_set: StackSetSummaryTypeDef) -> Dict[Literal["Instances"], List[StackInstanceSummaryTypeDef]]:
    pages = cfn.get_paginator("list_stack_instances").paginate(StackSetName=stack_set["StackSetId"])
    instances = [inst for page in pages for inst in page["Summaries"]]
    return {"Instances": instances}


def list_operations(cfn: CloudFormationClient, stack_set: StackSetSummaryTypeDef) -> Dict[Literal["Operations"], List[StackSetOperationSummaryTypeDef]]:
    pages = cfn.get_paginator("list_stack_set_operations").paginate(StackSetName=stack_set["StackSetId"])
    operations = [op for page in pages for op in page["Summaries"]]
    return {"Operations": operations}


def describe_stack_set(cfn: CloudFormationClient, stack_set: StackSetSummaryTypeDef) -> StackSetTypeDef:
    description = cfn.describe_stack_set(StackSetName=stack_set["StackSetId"])["StackSet"]
    return description


def dump_snapshot_to_json(snapshot: Any) -> Any:

    class DateEncoder(json.JSONEncoder):
        
        def default(self, obj: Any) -> Any:
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            return json.JSONEncoder.default(self, obj)

    json.dump(snapshot, sys.stdout, cls=DateEncoder)


if __name__ == "__main__":
    main()
