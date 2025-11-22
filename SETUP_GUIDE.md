# TMF921 Dataset Generator - Setup Guide

##Step 1: Get Your Free Groq API Key

1. **Visit Groq Console**: https://console.groq.com/
2. **Sign Up**: Create a free account (no credit card required)
3. **Create API Key**:
   - Click on "API Keys" in the left sidebar
   - Click "Create API Key"
   - Give it a name (e.g., "TMF921 Dataset Generator")
   - **Copy the API key** - you won't be able to see it again!

## Step 2: Configure Environment

Create a file named `.env` in `d:\dataset\` with this content:

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Replace the `gsk_xxx...` with your actual Groq API key.

## Step 3: Verify Installation

Open PowerShell in `d:\dataset\` and run:

```powershell
python llm_interface.py
```

You should see:
```
✓ Initialized groq with model: llama-3.1-70b-versatile
✓ Test generation successful:
{"message": "Hello, World!"}
```

## Step 4: Run Pilot Test (10 intents)

Test the system with the first 10 intents:

```powershell
python generate_dataset.py --max 10
```

Expected output:
```
==============================================================
TMF921 DATASET GENERATOR
==============================================================
Provider: groq
Start Index: 0
Max Intents: 10
==============================================================

Generating TMF921 intents: 100%|██████████| 10/10 [00:25<00:00,  2.50s/intent]

✓ Dataset saved successfully
==============================================================
GENERATION SUMMARY
==============================================================
Total Intents Processed: 10
Successful: 10
Failed: 0
Success Rate: 100.0%
Model Used: groq:llama-3.1-70b-versatile
Output File: output\tmf921_dataset.json
==============================================================
```

Check the output:
- `output/tmf921_dataset.json` - Your dataset
- `output/generation_log.txt` - Detailed logs

## Step 5: Generate Full Dataset (All 830 intents)

Once the pilot test looks good, generate the complete dataset:

```powershell
python generate_dataset.py
```

This will take approximately **1-3 hours** depending on Groq's response times.

### Features During Generation:

- **Progress bar** shows real-time progress
- **Checkpoints** saved every 50 intents to `output/checkpoints/`
- **Logs** written to `output/generation_log.txt`
- **Can interrupt** with Ctrl+C and resume later

### To Resume After Interruption:

```powershell
# If you stopped at intent 250
python generate_dataset.py --start 250
```

## Step 6: Review Output

After completion, review:

1. **`output/tmf921_dataset.json`** - Main dataset file
2. **`output/generation_log.txt`** - Detailed logs
3. **`output/failed_intents.json`** - Any failed intents (hopefully empty!)

## Troubleshooting

### "GROQ_API_KEY not found"
- Make sure `.env` file exists in `d:\dataset\`
- Check that there are no typos in the filename (must be exactly `.env`)
- Verify the API key is correct

### "Module not found" errors
Run:
```powershell
pip install -r requirements.txt
```

### Rate Limit Errors
- Groq's free tier is very generous
- The script has automatic retry logic
- If you hit limits, wait a few minutes and resume with `--start`

### JSON Parse Errors
- The script has template fallback
- Check `generation_log.txt` for details
- Failed intents will use template-based generation

## Tips for Best Results

1. **Run overnight**: The full generation takes 1-3 hours
2. **Check pilot first**: Always test with `--max 10` before full run
3. **Monitor logs**: Tail the log file to watch progress
   ```powershell
   Get-Content output\generation_log.txt -Wait
   ```
4. **Use checkpoints**: Don't hesitate to stop and resume

## Support

If you encounter issues:
1. Check `generation_log.txt` for detailed error messages
2. Test individual components (`python llm_interface.py`, etc.)
3. Verify your API key is valid at https://console.groq.com/

---

**Ready to start?** Follow Step 1 to get your Groq API key!
