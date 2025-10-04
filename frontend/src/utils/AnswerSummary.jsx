const AnswerSummary = ({ answer }) => {
    if (!answer) return null;

    return (
        <div className="mt-4">
            <div className="max-w-2xl mx-auto bg-gradient-to-br from-gray-50 to-white border border-gray-200 p-5 md:p-6 rounded-xl shadow-sm">
                <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <span className="bg-indigo-100 text-indigo-800 p-2 rounded-lg">📄</span>
                    <span>Summary</span>
                </h2>
                <div className="prose prose-indigo max-w-none text-gray-700 overflow-y-auto max-h-[60vh]">
                    {answer.split('\n').map((paragraph, index) => (
                        <p key={index} className="mb-3 last:mb-0">
                            {paragraph}
                        </p>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default AnswerSummary;
