import React, { useState } from "react";

function AddNumbers() {
  // State to store the list of values from the textboxes
  const [values, setValues] = useState([0]);

  // Add a new textbox by appending a new value to the list
  const addTextbox = () => {
    setValues([...values, 0]); // Adds a new textbox with a default value of 0
  };

  // Remove a textbox at a specific index
  const removeTextbox = (index) => {
    const newValues = [...values];
    newValues.splice(index, 1); // Remove the value at the given index
    setValues(newValues);
    };

  // Handle changes in the textboxes
  const handleInputChange = (index, event) => {
    const newValues = [...values];
    newValues[index] = event.target.value === "" ? "" : parseFloat(event.target.value) || 0; // Update the value or set to 0 if not a valid number
    setValues(newValues);
  };

  // Consolidate the values into the desired JSON format and log it
  const handleSubmit = async (event) => {
    event.preventDefault();
    const jsonData = {
      time_stamp: new Date().toISOString(),
      data: values.map(Number),
    };
  
    try {
      const token = localStorage.getItem('token'); 
      const response = await fetch("https://python-api-360127904619.europe-west3.run.app/upload/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(jsonData),
      });
  
      const result = await response.json();
      alert(`Success! File saved as ${result.file_name}`);
    } catch (error) {
      console.error("Error:", error);
      alert("Failed to upload JSON data");
    }
  };
  

  return (
    <div style={{ padding: "20px" }}>
      <h2>Add your numbers</h2>
      <form onSubmit={handleSubmit}>
        {values.map((value, index) => (
          <div key={index} style={{ marginBottom: "10px" }}>
            <input
              type="number"
              value={value}
              onChange={(e) => handleInputChange(index, e)}
              placeholder={`Value ${index + 1}`}
              required
              style={{ width: "300px", padding: "5px", fontSize: "16px" }}
            />
            {/* Add a remove button next to each input (except the first textbox if only one is left) */}
            {values.length > 1 && (
              <button
                type="button"
                onClick={() => removeTextbox(index)}
                style={{ color: 'red' }}
              >
                Remove
              </button>
            )}
          </div>
        ))}
        <button type="button" onClick={addTextbox} style={{ marginRight: "10px" }}>
          Add Textbox
        </button>
        <button type="submit">Submit</button>
      </form>
    </div>
  );
}

export default AddNumbers;