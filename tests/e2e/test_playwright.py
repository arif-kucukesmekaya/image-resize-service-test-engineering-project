# Bu dosya: Playwright ile E2E tarayıcı testleri
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
def test_upload_and_see_result(page: Page, live_server, sample_image_bytes):
    """Scenario 1: Uploads a sample image, fills out parameters, clicks resize, and asserts the success result card is shown."""
    page.goto(live_server)

    # Use Playwright set_input_files with buffer dict
    page.set_input_files("#file-input", files={
        "name": "sample.jpg",
        "mimeType": "image/jpeg",
        "buffer": sample_image_bytes
    })

    # Set parameters
    page.fill("#width-input", "300")
    page.fill("#height-input", "300")
    page.select_option("#format-select", "JPEG")

    # Click resize button
    page.click("#resize-btn")

    # Wait and check result
    result_card = page.locator("[data-testid='result-card']")
    expect(result_card).to_be_visible()
    expect(result_card).to_contain_text("Image successfully resized!")

@pytest.mark.e2e
def test_list_images_after_upload(page: Page, live_server, sample_image_bytes):
    """Scenario 2: Uploads an image, clicks to refresh list, and verifies the image table has at least one row."""
    page.goto(live_server)

    page.set_input_files("#file-input", files={
        "name": "sample.jpg",
        "mimeType": "image/jpeg",
        "buffer": sample_image_bytes
    })
    page.click("#resize-btn")

    # Wait for resize to complete
    page.wait_for_selector("[data-testid='result-card']")

    # Click refresh list
    page.click("#list-btn")

    # Verify at least one row with data-testid="image-row"
    rows = page.locator("[data-testid='image-row']")
    expect(rows.first).to_be_visible()

@pytest.mark.e2e
def test_delete_image(page: Page, live_server, sample_image_bytes):
    """Scenario 3: Uploads an image, refreshes list, clicks delete, accepts the confirm dialog, and verifies the row is removed."""
    page.goto(live_server)

    page.set_input_files("#file-input", files={
        "name": "sample.jpg",
        "mimeType": "image/jpeg",
        "buffer": sample_image_bytes
    })
    page.click("#resize-btn")

    # Wait for upload, then refresh
    page.wait_for_selector("[data-testid='result-card']")
    page.click("#list-btn")

    # Expect at least one row initially
    rows = page.locator("[data-testid='image-row']")
    expect(rows.first).to_be_visible()
    initial_count = rows.count()

    # Intercept dialog and accept it automatically
    page.on("dialog", lambda dialog: dialog.accept())

    # Click delete button on the first row
    page.locator(".delete-btn").first.click()

    # Wait for the row count to decrease
    page.wait_for_timeout(500)

    # Verify count has decreased
    final_count = rows.count()
    assert final_count < initial_count
