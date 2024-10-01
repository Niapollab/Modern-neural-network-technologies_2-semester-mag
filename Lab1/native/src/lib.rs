use pyo3::prelude::pymodule;

#[pymodule]
mod native {
    use pyo3::prelude::*;
    use rand::random;

    #[pyclass]
    struct RosenblattNeuron;

    #[pymethods]
    impl RosenblattNeuron {
        #[new]
        fn new() -> Self {
            RosenblattNeuron
        }

        fn predict(&self, input: Vec<f64>) -> PyResult<Vec<f64>> {
            let predictions: Vec<f64> = (0..input.len()).map(|_| random()).collect();
            Ok(predictions)
        }

        fn evaluate(&self, input: Vec<f64>, expected_output: Vec<f64>) -> PyResult<()> {
            Ok(())
        }
    }

    #[pyclass]
    struct RosenblattNeuronSerializer;

    #[pymethods]
    impl RosenblattNeuronSerializer {
        #[new]
        fn new() -> Self {
            RosenblattNeuronSerializer
        }

        fn load(&self, filename: String) -> PyResult<RosenblattNeuron> {
            Ok(RosenblattNeuron::new())
        }

        fn save(&self, filename: String, model: &RosenblattNeuron) -> PyResult<()> {
            Ok(())
        }

        fn build(&self) -> PyResult<RosenblattNeuron> {
            Ok(RosenblattNeuron::new())
        }
    }
}
