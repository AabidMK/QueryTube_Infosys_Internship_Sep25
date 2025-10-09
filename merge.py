import pandas as pd

# Load the datasets
video_df = pd.read_csv('video_with_transcript_flag.csv')
transcript_df = pd.read_csv('cleaned_transcript_details.csv')

# Filter for videos with transcripts
video_with_transcript = video_df[video_df['transcript_flag'] == True]

# Merge the two dataframes on the 'id' column
merged_df = pd.merge(video_with_transcript, transcript_df, on='id')

merged_df['merged_transcript'] = merged_df['title'] + ' ' + merged_df['transcript']

merged_df.drop(columns=['transcript'], inplace=True)

# Save the merged dataframe to a new CSV file
merged_df.to_csv('video_with_transcript.csv', index=False)

print("Successfully created 'video_with_transcript.csv'")