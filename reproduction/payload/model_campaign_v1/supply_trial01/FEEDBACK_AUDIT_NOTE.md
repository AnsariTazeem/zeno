# Public threshold provenance in the frozen feedback

During transcript inspection, the native failed_checks records were confirmed
to contain a `source` number as well as the candidate value and acceptance
limit. The frozen serializer includes those records in the measured feedback.

These numbers (for example 75.71 dB gain, 58.6 degrees PM and 19.8 dB GM) are
the public AnalogPortBench threshold-derivation metadata in the pinned
analog_public_v1/upstream/benchmark/circuits/opamp_2stg/spec.yaml. They are not
the newly run three-supply reference-control measurements or a private circuit
repair. No reference netlist or component values are supplied by this field.

Nevertheless, feedback contains these public rubric-provenance values in
addition to the current candidate's measurements. Disclose that detail when
describing the condition rather than claiming that every feedback number is
newly measured from the candidate. The frozen serializer is left unchanged
during this trajectory. A later collection version may omit unnecessary
provenance fields prospectively; it must not rewrite this trial's sent inputs.
