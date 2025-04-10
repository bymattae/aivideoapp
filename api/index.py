def handler(request):
    """
    Simple health check endpoint
    """
    if request.method == "GET":
        return {
            "statusCode": 200,
            "body": "API is running"
        }
    return {
        "statusCode": 405,
        "body": "Method not allowed"
    } 