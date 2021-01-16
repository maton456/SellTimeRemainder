import json
import boto3
from scraping import get_price
import datetime

def add_price(card, owner, date, price):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('SellTimeRemainder')

    response = table.update_item(
        Key={
            'Card': card,
            'Owner': owner
        },
        UpdateExpression="set Prices.#date=:p",
        ExpressionAttributeNames={
            '#date': date
        },
        ExpressionAttributeValues={
            ':p': price,
        },
        ReturnValues="UPDATED_NEW"
    )
    return response

def lambda_handler(event, context):
    # TODO implement
    
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('SellTimeRemainder')
    
    resp = table.scan()
    
    #print(resp['Items'])
    
    for item in resp['Items']:
        print(item)
        response = add_price(item['Card'],
                            item['Owner'],
                            str(datetime.date.today()),
                            get_price(item['URL']),
                            )
        print(response)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
