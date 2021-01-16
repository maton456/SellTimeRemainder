import json
import boto3

def put_card(card, owner, url):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('SellTimeRemainder')
    
    response = table.put_item(
       Item={
            'Card': card,
            'Owner': owner,
            'URL': url,
            'Prices': dict()
        }
    )
    return response
    
def lambda_handler(event, context):
    # TODO implement
    
    response = put_card(event['card'], event['owner'], event['url'])
    
    print(response)
    

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
