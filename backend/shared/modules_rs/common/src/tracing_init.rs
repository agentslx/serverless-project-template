use std::env;
use opentelemetry::global;
use opentelemetry::trace::TracerProvider as _;
use opentelemetry_aws::trace::{XrayIdGenerator, XrayPropagator};
use opentelemetry_sdk::trace::{SdkTracerProvider, Sampler};
use tracing_opentelemetry::OpenTelemetryLayer;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};

pub fn init_tracing() {
    let level = env::var("LOG_LEVEL").unwrap_or_else(|_| "info".into());

    global::set_text_map_propagator(XrayPropagator::default());

    let provider = SdkTracerProvider::builder()
        .with_id_generator(XrayIdGenerator::default())
        .with_sampler(Sampler::AlwaysOn)
        .build();

    let tracer = provider.tracer("lambda");
    global::set_tracer_provider(provider);

    let fmt_layer = tracing_subscriber::fmt::layer()
        .json()
        .with_target(false)
        .with_current_span(false);

    let otel_layer = OpenTelemetryLayer::new(tracer);

    tracing_subscriber::registry()
        .with(EnvFilter::new(&level))
        .with(fmt_layer)
        .with(otel_layer)
        .try_init()
        .ok();
}
