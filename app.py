// ... existing imports and code ...

// Ensure transactions are sorted by timestamp (createdAt) in descending order
const sortedTransactions = transactions.sort((a, b) => {
    const aCreated = a.createdAt ? new Date(a.createdAt) : new Date().getTime();
    const bCreated = b.createdAt ? new Date(b.createdAt) : new Date().getTime();
    return bCreated - aCreated; // descending order
});

// ... rest of your code ...
