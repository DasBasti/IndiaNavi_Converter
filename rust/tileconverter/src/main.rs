use lambda_http::{run, service_fn, Body, Error, Request, RequestExt, Response};
use rand::thread_rng;
use rand::prelude::SliceRandom;

const urls : [&str; 3] = ["https://a.tile.opentopomap.org","https://b.tile.opentopomap.org","https://c.tile.opentopomap.org",]; 
/// This is the main body for the function.
/// Write your code inside it.
/// There are some code example in the following URLs:
/// - https://github.com/awslabs/aws-lambda-rust-runtime/tree/main/examples
async fn function_handler(event: Request) -> Result<Response<Body>, Error> {
    let mut rng = thread_rng();
    let online_addr = format!("{:?}{}", urls.choose(&mut rng), event.raw_http_path());
    let resp = reqwest::get(&online_addr).await?;

    let image = indianavi_map_color::convert_image(&resp.bytes().await?)?;
    println!("Get {}", &online_addr);
    Ok(Response::builder()
        .status(200)
        .header("content-type", "application/binary")
        .body(Body::Binary(image))
        .map_err(Box::new)?)
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        // disable printing the name of the module in every log line.
        .with_target(false)
        // disabling time is handy because CloudWatch will add the ingestion time.
        .without_time()
        .init();

    run(service_fn(function_handler)).await
}
