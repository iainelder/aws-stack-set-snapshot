import boto3
from boto_collator_client import CollatorClient
from pprint import pprint
import json
import sys


def main():
    session = boto3.Session()
    cfn = CollatorClient(session.client("cloudformation", region_name="eu-west-1"))
    
    stack_sets = cfn.list_stack_sets()["Summaries"]
    
    for s in stack_sets:
        s["Instances"] = cfn.list_stack_instances(StackSetName=s["StackSetId"])["Summaries"]
    
    #pprint(stack_sets)
    json.dump(stack_sets, sys.stdout)


if __name__ == "__main__":
    main()
