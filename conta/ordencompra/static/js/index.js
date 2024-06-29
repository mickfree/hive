const listItems = async () => {
    try {
        const response = await fetch("http://127.0.0.1:8000/ordencompra/list_items/");
        const data = await response.json();

        let content=``;

        data.itemsordenventa.array.forEach(itemsordenventa, index => {
            let content = `
            <tr>
                <td>${index}</td>
                <td>${itemsordenventa.cantidad}</td>
                <td>${itemsordenventa.id}</td>
            </tr>
            `;
            
        });
        
    } catch (ex) {
        alert(ex);
    }
};

window.addEventListener("load", async () => {
    await listItems();
});
