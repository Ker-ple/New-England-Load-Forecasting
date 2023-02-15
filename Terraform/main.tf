locals {
  definition_template = <<EOF
{
  "Comment": "A description of my state machine",
  "StartAt": "Split date range",
  "States": {
    "Split date range": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$.Payload",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "arn:aws:lambda:us-east-1:485809471371:function:coherent-oriole-lambda-from-container-image:$LATEST"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 2,
          "MaxAttempts": 6,
          "BackoffRate": 2
        }
      ],
      "Next": "Map"
    },
    "Map": {
      "Type": "Map",
      "ItemProcessor": {
        "ProcessorConfig": {
          "Mode": "INLINE"
        },
        "StartAt": "Parallel",
        "States": {
          "Parallel": {
            "Type": "Parallel",
            "Branches": [
              {
                "StartAt": "Extract Load_Forecast",
                "States": {
                  "Extract Load_Forecast": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::lambda:invoke",
                    "OutputPath": "$.Payload",
                    "Parameters": {
                      "Payload.$": "$",
                      "FunctionName": "arn:aws:lambda:us-east-1:485809471371:function:pure-crab-lambda-from-container-image:$LATEST"
                    },
                    "Retry": [
                      {
                        "ErrorEquals": [
                          "Lambda.ServiceException",
                          "Lambda.AWSLambdaException",
                          "Lambda.SdkClientException",
                          "Lambda.TooManyRequestsException"
                        ],
                        "IntervalSeconds": 2,
                        "MaxAttempts": 6,
                        "BackoffRate": 2
                      }
                    ],
                    "End": true
                  }
                }
              },
              {
                "StartAt": "Extract Load_Actual",
                "States": {
                  "Extract Load_Actual": {
                    "Type": "Task",
                    "Resource": "arn:aws:states:::lambda:invoke",
                    "OutputPath": "$.Payload",
                    "Parameters": {
                      "Payload.$": "$",
                      "FunctionName": "arn:aws:lambda:us-east-1:485809471371:function:loved-stingray-lambda-from-container-image:$LATEST"
                    },
                    "Retry": [
                      {
                        "ErrorEquals": [
                          "Lambda.ServiceException",
                          "Lambda.AWSLambdaException",
                          "Lambda.SdkClientException",
                          "Lambda.TooManyRequestsException"
                        ],
                        "IntervalSeconds": 2,
                        "MaxAttempts": 6,
                        "BackoffRate": 2
                      }
                    ],
                    "End": true
                  }
                }
              }
            ],
            "End": true
          }
        }
      },
      "End": true
    }
  }
}
EOF
}

module "step-functions" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "2.7.3"

  name = random_pet.this.id

  type = "STANDARD"

  definition = local.definition_template

  logging_configuration = {
    include_execution_data = true
    level                  = "ALL"
  }

  service_integrations = {

    lambda = {
      lambda = [
        module.extract_weather_lambda.lambda_function_arn, "arn:aws:lambda:us-east-1:485809471371:function:adapting-octopus-lambda-from-container-image"
      ]

      lambda = [
        module.iso_ne_extract_load_lambda.lambda_function_arn, "arn:aws:lambda:us-east-1:485809471371:function:loved-stingray-lambda-from-container-image"
      ]

      lambda = [
        module.iso_ne_extract_forecast_lambda.lambda_function_arn, "arn:aws:lambda:us-east-1:485809471371:function:pure-crab-lambda-from-container-image"
      ]

      lambda = [
        module.date_split_lambda.lambda_function_arn, "arn:aws:lambda:us-east-1:485809471371:function:coherent-oriole-lambda-from-container-image"
      ]
    }

    stepfunction_Sync = {
      stepfunction          = ["arn:aws:states:us-east-1:485809471371:stateMachine:test_state_machine"]
      stepfunction_Wildcard = ["arn:aws:states:us-east-1:485809471371:stateMachine:test_state_machine"]

      # Set to true to use the default events (otherwise, set this to a list of ARNs; see the docs linked in locals.tf
      # for more information). Without events permissions, you will get an error similar to this:
      #   Error: AccessDeniedException: 'arn:aws:iam::xxxx:role/step-functions-role' is not authorized to
      #   create managed-rule
      events = true
    }

    #    # NB: This will "Deny" everything (including logging)!
    #    no_tasks = {
    #      deny_all = true
    #    }
  }

  tags = {
    Module = "step_function"
  }
}

resource "random_pet" "this" {
  length = 2
}