const handleSubmit = async (e, query, setLoading, setAnswer) => {
    e.preventDefault();
    setLoading(true);
    try {
        const res = await fetch('http://localhost:8000/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: query }),
        });
        const data = await res.json();
        setAnswer(data.answer);
    } catch (error) {
        console.error('Error during fetch:', error);
    } finally {
        setLoading(false);
    }
};

export default handleSubmit;
