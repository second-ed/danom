use pyo3::prelude::*;

use crate::core::stream::Stream;
pub mod core;

/// Python module implemented in Rust.
#[pymodule]
fn _rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Stream>()?;
    Ok(())
}
