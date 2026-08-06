use pyo3::prelude::*;
use pyo3::types::{PyTuple, PyType};

#[derive(Debug)]
enum Operation {
    Map(Py<PyAny>),
    Filter(Py<PyAny>),
}

impl Operation {
    fn clone_ref(&self, py: Python<'_>) -> Self {
        match self {
            Self::Map(function) => Self::Map(function.clone_ref(py)),
            Self::Filter(predicate) => Self::Filter(predicate.clone_ref(py)),
        }
    }
}

/// A small Python-facing stream backed by Rust.
///
/// The values remain Python objects, so Python callables can be used with
/// `map` and `filter`.
#[pyclass(name = "Stream")]
pub struct Stream {
    seq: Vec<Py<PyAny>>,
    ops: Vec<Operation>,
}

#[pymethods]
impl Stream {
    /// Create a stream from any Python iterable.
    #[classmethod]
    pub fn from_iterable(_cls: &Bound<'_, PyType>, iterable: &Bound<'_, PyAny>) -> PyResult<Self> {
        let iterator = iterable.try_iter()?;
        let mut seq = Vec::new();

        for item in iterator {
            seq.push(item?.unbind());
        }

        Ok(Self {
            seq,
            ops: Vec::new(),
        })
    }

    /// Apply a Python function to every item and return a new stream.
    pub fn map(&self, py: Python<'_>, function: &Bound<'_, PyAny>) -> PyResult<Self> {
        let mut ops = clone_operations(&self.ops, py);

        ops.push(Operation::Map(function.clone().unbind()));

        Ok(Self {
            seq: self.seq.iter().map(|item| item.clone_ref(py)).collect(),
            ops,
        })
    }

    /// Keep the seq for which a Python predicate returns true.
    pub fn filter(&self, py: Python<'_>, function: &Bound<'_, PyAny>) -> PyResult<Self> {
        let mut ops = clone_operations(&self.ops, py);

        ops.push(Operation::Filter(function.clone().unbind()));

        Ok(Self {
            seq: self.seq.iter().map(|item| item.clone_ref(py)).collect(),
            ops,
        })
    }

    /// Materialize the stream as a Python list.
    pub fn collect(&self, py: Python<'_>) -> PyResult<Py<PyTuple>> {
        let seq = self
            .seq
            .iter()
            .map(|item| apply_operations(py, item, &self.ops))
            .collect::<PyResult<Vec<_>>>()?
            .into_iter()
            .flatten()
            .collect::<Vec<_>>();
        Ok(PyTuple::new(py, &seq)?.unbind())
    }

    pub fn __len__(&self) -> usize {
        self.seq.len()
    }

    pub fn __bool__(&self) -> bool {
        !self.seq.is_empty()
    }
}

fn clone_operations(operations: &[Operation], py: Python<'_>) -> Vec<Operation> {
    operations
        .iter()
        .map(|operation| operation.clone_ref(py))
        .collect()
}

fn apply_operations(
    py: Python<'_>,
    original: &Py<PyAny>,
    operations: &[Operation],
) -> PyResult<Option<Py<PyAny>>> {
    let mut value = original.clone_ref(py);

    for operation in operations {
        match operation {
            Operation::Map(function) => {
                let next = function.bind(py).call1((value.bind(py),))?;

                value = next.unbind();
            }

            Operation::Filter(predicate) => {
                let keep = predicate.bind(py).call1((value.bind(py),))?.is_truthy()?;

                if !keep {
                    return Ok(None);
                }
            }
        }
    }

    Ok(Some(value))
}
