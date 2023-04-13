import requests
from tqdm import tqdm
import time
import os
import xarray as xr
import numpy as np


def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.2f} {unit}"


def download(url, filename, max_retries=3, retry_wait=5):
    """
    Download a file from a URL with retries on connection issues.

    Parameters:
    url (str): The URL of the file to download.
    filename (str): The local path where the downloaded file will be saved.
    max_retries (int): The maximum number of retries on connection issues. Default is 3.
    retry_wait (int): The number of seconds to wait between retries. Default is 5.

    Returns:
    None
    """
    print("Downloading", filename)
    retries = 0
    total_size = 0
    r = None

    while retries <= max_retries:
        try:
            # Send a GET request and stream the response content
            r = requests.get(url, stream=True)
            total_size, block_size = int(
                r.headers.get('content-length', 0)), 1024

            # Save the content to the specified file
            with open(filename, 'wb') as f:
                for data in tqdm(r.iter_content(block_size),
                                 total=total_size // block_size,
                                 unit='KiB', unit_scale=True):
                    f.write(data)
            break
        except Exception as e:
            # Handle connection-related issues and retry the download
            if isinstance(e, (requests.exceptions.ConnectionError, ConnectionResetError)):
                retries += 1
                if retries > max_retries:
                    print(
                        f"Failed to download {filename} after {max_retries} retries.")
                    break
                else:
                    print(
                        f"Connection issue, retrying download in {retry_wait} seconds... (attempt {retries}/{max_retries})")
                    time.sleep(retry_wait)
            # Handle other unexpected errors
            else:
                print(
                    f"An unexpected error occurred while downloading {filename}: {e}")
                break

    # Check if the downloaded file size matches the expected size
    if r is not None and total_size != 0 and os.path.getsize(filename) != total_size:
        print("Downloaded size does not match expected size!\n",
              "FYI, the status code was", r.status_code)



region_polygons = {
    'med': [(-6, 30), (-5.31, 41), (13.66, 47.29), (39, 38.2), (36, 30)]
}

def crop_by_polygon(ds, polygon='med'):
    """
    Crop an xarray dataset by a specified polygon.

    Parameters:
    ds (xarray.Dataset): The dataset to be cropped.
    polygon (list of tuples or str): A list of longitude and latitude tuples defining the polygon,
                                     or a predefined string 'med' for the Mediterranean Sea.
                                     Default is 'med'.

    Returns:
    xarray.Dataset: The cropped dataset.
    """

    # 1. Convert the longitude coordinates to a -180 to 180 range
    ds['longitude'] = xr.where(
        ds['longitude'] > 180, ds['longitude'] - 360, ds['longitude'])

    # Define the polygon for the selected region
    if isinstance(polygon, str):
        polygon = region_polygons[polygon]

    # 2. Crop the dataset to the region of interest
    # We first crop into a square defined by the minimum and maximum longitude and latitude values
    # of the polygon. This way we reduce the size of the dataset and speed up the computation.
    min_lon = min(p[0] for p in polygon)
    max_lon = max(p[0] for p in polygon)
    min_lat = min(p[1] for p in polygon)
    max_lat = max(p[1] for p in polygon)

    ds = ds.where((ds['longitude'] >= min_lon) & (ds['longitude'] <= max_lon) &
                  (ds['latitude'] >= min_lat) & (ds['latitude'] <= max_lat), drop=True)

    # Define a function to check if a point is inside the polygon
    def point_in_polygon(lon, lat):
        # Add the first point to the end of the list to close the polygon
        polygon.append(polygon[0])

        inside = False
        for i in range(len(polygon) - 1):
            if ((polygon[i][1] <= lat < polygon[i+1][1]) or (polygon[i+1][1] <= lat < polygon[i][1])) and \
                    (lon < (polygon[i+1][0] - polygon[i][0]) * (lat - polygon[i][1]) / (polygon[i+1][1] - polygon[i][1]) + polygon[i][0]):
                inside = not inside
        return inside

    # Vectorize the function so it can be applied element-wise to arrays
    point_in_polygon_vec = np.vectorize(point_in_polygon)

    # Use apply_ufunc to create a mask for the dataset
    mask = xr.apply_ufunc(point_in_polygon_vec,
                          ds['longitude'], ds['latitude'])

    # Apply the mask to the dataset, removing points outside the polygon
    ds_crop = ds.where(mask, drop=True)

    return ds_crop
