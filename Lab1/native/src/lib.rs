use pyo3::prelude::pymodule;

#[pymodule]
mod native {
    use pyo3::{exceptions::PyValueError, prelude::*, PyResult};
    use rand::{thread_rng, Rng};
    use serde::{Deserialize, Serialize};
    use std::{
        fs::File,
        io::{Read, Write},
    };

    #[pyclass]
    #[derive(Serialize, Deserialize)]
    struct RosenblattNeuron {
        weights: Vec<f64>,
        bias: f64,
        learning_rate: f64,
    }

    #[pymethods]
    impl RosenblattNeuron {
        #[new]
        fn new(weights: Vec<f64>, bias: f64, learning_rate: f64) -> Self {
            RosenblattNeuron {
                weights,
                bias,
                learning_rate,
            }
        }

        fn predict(&self, input: Vec<f64>) -> PyResult<Vec<f64>> {
            let prediction = self.internal_predict(&input)?;

            Ok(vec![prediction])
        }

        fn evaluate(&mut self, input: Vec<f64>, expected_output: Vec<f64>) -> PyResult<()> {
            if expected_output.len() != 1 {
                return Err(PyValueError::new_err(format!(
                    "Expected output vector length \"{}\" must be equals 1.",
                    expected_output.len(),
                )));
            }

            let prediction = self.internal_predict(&input)?;
            let expected_output = expected_output.into_iter().next().unwrap();

            let error = expected_output - prediction;
            for (weight, input_value) in self.weights.iter_mut().zip(&input) {
                *weight += self.learning_rate * error * input_value;
            }
            self.bias += self.learning_rate * error;

            Ok(())
        }
    }

    impl RosenblattNeuron {
        #[inline]
        fn internal_predict(&self, input: &Vec<f64>) -> PyResult<f64> {
            if input.len() != self.weights.len() {
                return Err(PyValueError::new_err(format!(
                    "Input vector length \"{}\" does not match the number of weights \"{}\".",
                    input.len(),
                    self.weights.len()
                )));
            }

            Ok(Self::heaviside(
                self.weights
                    .iter()
                    .zip(input)
                    .map(|(w, i)| w * i)
                    .sum::<f64>()
                    + self.bias,
            ))
        }

        #[inline]
        fn heaviside(x: f64) -> f64 {
            if x >= 0.0 {
                1.0
            } else {
                0.0
            }
        }
    }

    #[pyclass]
    struct RosenblattNeuronSerializer {
        size: u32,
        bias: f64,
    }

    #[pymethods]
    impl RosenblattNeuronSerializer {
        #[new]
        fn new(size: u32, bias: f64) -> Self {
            RosenblattNeuronSerializer { size, bias }
        }

        fn load(&self, filename: String) -> PyResult<RosenblattNeuron> {
            let mut file = File::open(&filename).map_err(|_| {
                PyValueError::new_err(format!("Failed to open file \"{filename}\"."))
            })?;

            let mut buffer = vec![];
            file.read_to_end(&mut buffer).map_err(|_| {
                PyValueError::new_err(format!("Failed to read file \"{filename}\"."))
            })?;

            let model: RosenblattNeuron = bincode::deserialize(&buffer)
                .map_err(|_| PyValueError::new_err(format!("Failed to deserialize model.")))?;

            Ok(model)
        }

        fn save(&self, filename: String, model: &RosenblattNeuron) -> PyResult<()> {
            let buffer = bincode::serialize(model)
                .map_err(|_| PyValueError::new_err(format!("Failed to serialize model.")))?;

            let mut file = File::create(&filename).map_err(|_| {
                PyValueError::new_err(format!("Failed to create file \"{filename}\"."))
            })?;
            file.write_all(&buffer).map_err(|_| {
                PyValueError::new_err(format!("Failed to write to file \"{filename}\"."))
            })?;

            Ok(())
        }

        fn build(&self) -> PyResult<RosenblattNeuron> {
            let mut rand_provider = thread_rng();
            let weights = (0..self.size)
                .map(|_| rand_provider.gen_range(-0.3..=0.3))
                .collect();

            Ok(RosenblattNeuron::new(weights, self.bias, 0.5))
        }
    }
}
