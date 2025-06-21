document.addEventListener('DOMContentLoaded', function() {
    const radiologyForm = document.getElementById('radiologyForm');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultCard = document.getElementById('resultCard');
    const noResultMsg = document.getElementById('noResultMsg');
    const simplifiedText = document.getElementById('simplifiedText');
    const audioPlayer = document.getElementById('audioPlayer');
    const copyTextBtn = document.getElementById('copyTextBtn');
    const downloadAudioBtn = document.getElementById('downloadAudioBtn');
    const keyFindingsCard = document.getElementById('keyFindingsCard');
    const keyFindings = document.getElementById('keyFindings');
    const noFindingsMsg = document.getElementById('noFindingsMsg');
    const languageSelect = document.getElementById('language');
    const languageCodeInput = document.getElementById('language_code');

    // Handle language selection change
    languageSelect.addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        const langCode = selectedOption.getAttribute('data-code');
        languageCodeInput.value = langCode;
    });

    // Handle form submission
    radiologyForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading indicator
        loadingIndicator.style.display = 'block';
        resultCard.style.display = 'none';
        noResultMsg.style.display = 'none';
        keyFindingsCard.style.display = 'none';
        noFindingsMsg.style.display = 'block';
        
        // Get form data
        const formData = new FormData(radiologyForm);
        
        try {
            // Send request to simplify endpoint
            const response = await fetch('/simplify', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Server error: ' + response.status);
            }
            
            const data = await response.json();
            
            // Display simplified text
            simplifiedText.textContent = data.simplified_text;
            
            // Create audio player
            audioPlayer.innerHTML = `
                <audio controls class="w-100">
                    <source src="/static/audio/${data.audio_filename}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
            `;
            
            // Store audio filename for download
            downloadAudioBtn.setAttribute('data-filename', data.audio_filename);
            
            // Show result
            loadingIndicator.style.display = 'none';
            resultCard.style.display = 'block';
            noResultMsg.style.display = 'none';
            
            // Fetch key findings
            await fetchKeyFindings(data.original_text);
            
        } catch (error) {
            console.error('Error:', error);
            
            // Show error message
            loadingIndicator.style.display = 'none';
            noResultMsg.style.display = 'block';
            noResultMsg.innerHTML = `<p class="text-danger">Error: ${error.message}</p>`;
        }
    });
    
    // Fetch key findings from the radiology report
    async function fetchKeyFindings(text) {
        try {
            const response = await fetch('/api/key-findings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text })
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch key findings');
            }
            
            const data = await response.json();
            
            // Display key findings
            keyFindings.innerHTML = data.key_findings;
            keyFindingsCard.style.display = 'block';
            noFindingsMsg.style.display = 'none';
            
        } catch (error) {
            console.error('Error fetching key findings:', error);
            noFindingsMsg.style.display = 'block';
        }
    }
    
    // Copy simplified text to clipboard
    copyTextBtn.addEventListener('click', function() {
        const text = simplifiedText.textContent;
        navigator.clipboard.writeText(text).then(function() {
            // Show success message
            const originalText = copyTextBtn.textContent;
            copyTextBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyTextBtn.textContent = originalText;
            }, 2000);
        }, function(err) {
            console.error('Could not copy text: ', err);
        });
    });
    
    // Download audio file
    downloadAudioBtn.addEventListener('click', function() {
        const filename = this.getAttribute('data-filename');
        if (filename) {
            const link = document.createElement('a');
            link.href = `/static/audio/${filename}`;
            link.download = 'simplified_radiology_report.mp3';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    });
});
