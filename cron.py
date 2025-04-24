import cronitor
cronitor.api_key = 'c860ed6b660d45a998aed4620bd9e003'

# Create/update the monitor with proper notification settings
cronitor.Monitor.put(
    key='important-background-job',
    type='job',
    schedule='0 1 * * 1',
    notify=[]  # Wrap in a list (array)
)

# Optional: Decorate your function for telemetry
@cronitor.job('important-background-job')
def daily_metrics_task():
    try:
        print('Running daily metrics background job...')
        # Your job logic here
        
        # Notify success
        monitor = cronitor.Monitor('important-background-job')
        monitor.ping(state='complete')
    except Exception as e:
        # Notify failure
        monitor = cronitor.Monitor('important-background-job')
        monitor.ping(state='fail', message=f'Job failed: {str(e)}')
        raise  # Re-raise the exception if needed

# Example usage (if running manually)
if __name__ == '__main__':
    daily_metrics_task()