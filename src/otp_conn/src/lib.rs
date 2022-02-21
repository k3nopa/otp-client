#![allow(unused_assignments)]

use byteorder::{BigEndian, ReadBytesExt};
use pyo3::prelude::*;
use serialport;
use std::io;
use std::time::Duration;

#[derive(PartialEq)]
enum Status {
    SEND,
    RECV,
}

#[pyfunction]
fn recv_tree(mut layer: usize, height: usize) -> io::Result<Vec<Vec<u32>>> {
    let port_name = "/dev/ttyUSB0";
    let baud_rate = 115200;

    let builder = serialport::new(port_name, baud_rate)
        .stop_bits(serialport::StopBits::One)
        .data_bits(serialport::DataBits::Eight)
        .timeout(Duration::from_millis(10));

    let port = builder.open();

    let mut trees: Vec<Vec<u32>> = vec![];
    let mut status = Status::RECV;
    let total_keys = 2usize.pow(height as u32);

    match port {
        Ok(mut port) => {
            println!("UART on {} at {} baud:", &port_name, &baud_rate);
            let mut debug = true;

            while layer > 0 && debug {
                if status == Status::RECV {
                    let mut buf = [0; 4]; // Key size is 4 bytes.
                    let mut recv_data = 0;
                    let mut receiving = true;

                    while receiving {
                        match port.read(&mut buf) {
                            Ok(_) => {
                                let mut buffer = io::Cursor::new(buf);
                                recv_data = buffer.read_u32::<BigEndian>().unwrap();

                                status = Status::SEND;
                                receiving = false;
                            }
                            Err(ref e) if e.kind() == io::ErrorKind::TimedOut => {}
                            Err(e) => {
                                eprintln!("{:?}", e);
                                receiving = false;
                                debug = false;
                            }
                        }
                    }
                    // Empty tree or Completed latest layer.
                    if trees.len() == 0 || trees[trees.len() - 1].len() == total_keys {
                        let mut tree = vec![];
                        tree.push(recv_data);
                        trees.push(tree);
                    } else {
                        let trees_len = trees.len();
                        let tree = &mut trees[trees_len - 1];
                        tree.push(recv_data);
                    }
                }

                if status == Status::SEND {
                    port.write(&[1]).unwrap();
                    status = Status::RECV;
                }

                if trees[trees.len() - 1].len() == total_keys {
                    layer -= 1;
                }
            }
        }
        Err(e) => {
            eprintln!("Failed to open \"{}\". Error: {}", port_name, e);
            ::std::process::exit(1);
        }
    }

    Ok(trees)
}

#[pyfunction]
fn generate_otp_key(path: u8, k: u32) -> io::Result<String> {
    let port_name = "/dev/ttyUSB0";
    let baud_rate = 115200;

    let builder = serialport::new(port_name, baud_rate)
        .stop_bits(serialport::StopBits::One)
        .data_bits(serialport::DataBits::Eight)
        .timeout(Duration::from_millis(10));

    let port = builder.open();
    let mut otp_key = String::new();

    match port {
        Ok(mut port) => {
            // 1. Send path.
            port.write(&[path]).unwrap();

            let mut receiving = true;
            let mut layer = 0;
            // 2. Receive layer's length.
            let mut buf = [0; 4];
            while receiving {
                match port.read(&mut buf) {
                    Ok(_) => {
                        let mut buffer = io::Cursor::new(buf);
                        layer = buffer.read_u32::<BigEndian>().unwrap();
                        println!("Layer: {}", layer);
                        receiving = false;
                    }
                    Err(ref e) if e.kind() == io::ErrorKind::TimedOut => {}
                    Err(e) => {
                        eprintln!("{:?}", e);
                        receiving = false;
                    }
                }
            }

            // 3. Receive OTP key.
            let mut dbg = true;
            let mut failed = false;
            if layer < k {
                failed = true;
            }
            while layer > 0 && dbg {
                let mut status = Status::RECV;
                if status == Status::RECV {
                    let mut buf = [0; 4]; // Key size is 4 bytes.
                    let mut recv_key = String::new();
                    receiving = true;

                    while receiving {
                        match port.read(&mut buf) {
                            Ok(_) => {
                                if !failed {
                                    let mut buffer = io::Cursor::new(buf);
                                    let recv_data = buffer.read_u32::<BigEndian>().unwrap();
                                    recv_key = format!("{}", recv_data);
                                    otp_key.push_str(&recv_key);
                                } else {
                                    otp_key.push_str("");
                                }

                                status = Status::SEND;
                                receiving = false;
                            }
                            Err(ref e) if e.kind() == io::ErrorKind::TimedOut => {}
                            Err(e) => {
                                eprintln!("{:?}", e);
                                receiving = false;
                                dbg = false;
                            }
                        }
                    }
                }

                if status == Status::SEND {
                    port.write(&[1]).unwrap();
                    status = Status::RECV;
                }
                layer -= 1;
            }
        }
        Err(e) => {
            eprintln!("Failed to open \"{}\". Error: {}", port_name, e);
            ::std::process::exit(1);
        }
    }
    Ok(otp_key)
}

#[pymodule]
fn otp_conn(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(generate_otp_key, m)?)?;
    m.add_function(wrap_pyfunction!(recv_tree, m)?)?;
    Ok(())
}
