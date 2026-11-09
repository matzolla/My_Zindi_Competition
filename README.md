# Phase 1 training generator

Use this kit to generate labelled training episodes locally and run a CPU baseline. The competition Data tab provides the CSVs and the RGB-D inputs for Test.

## Generate training data

1. Extract this ZIP and read `simulator/README.md` and `THIRD_PARTY_NOTICES.md`. Set up the documented Linux x86-64 / Python 3.9 Habitat environment with an EGL renderer, and a separate Python 3.12 environment for the asset downloader and CPU baseline.
2. In the Python 3.12 environment, install `requirements-baseline.txt` and download the pinned simulator assets to a writable workspace, following `simulator/README.md`.
3. Open `GenerateTrain.ipynb` from the kit root. Set `SIM_PYTHON`, `SIM_WORKSPACE` and `RUN_SIMULATION=1` in the notebook environment. This produces two labelled episodes as a setup check. Use the full recipe in `simulator/README.md` and `TRAIN_GENERATION.json` for 864 episodes, or use a fresh seed and workspace for independent training data.

The generator writes `generated/Train.csv` and its matching `inputs/*.npz`. Use that CSV for training so its paths resolve to the generated observations. The `Train.csv` on Zindi documents the reference sample.

## Run the baseline and make a submission

Put `Test.csv` and the extracted `TestInputs/` folder beside each other. From the kit root, run the following with the Python 3.12 baseline environment active. Replace the two example paths with your actual paths.

```bash
python starter_baseline.py --train /path/to/workspace/generated/Train.csv \
  --test /path/to/competition-data/Test.csv --output baseline_run
```

Use a full training run for the baseline. The two-episode setup check only verifies the simulator. The command writes `baseline_run/Submission.csv` with the same IDs, order and columns as `SampleSubmission.csv`. Use Test observations for inference only. The baseline's local `validation_rmse` pools all prediction errors; the Zindi score is 1 minus the mean of the nine per-column RMSE values.

See `DataDescription.md` for the observation arrays and targets. Upstream 3D assets are downloaded separately under their applicable terms.
