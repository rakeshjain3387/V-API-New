docker run --rm -v $(pwd):/foo -w /foo lambci/lambda:build-python3.8 pip install -r requirements.txt -t layer/python/lib/python3.8/site-packages
cd layer
zip -r lambda_layer.zip *
rm -rf python