import { useState } from 'react';
import { Search } from 'lucide-react';
import { Input, Button, Card, CardContent } from '@/components/ui';

export default function SearchPage() {
    const [query, setQuery] = useState('');

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        // Implement search logic here
        console.log('Searching for:', query);
    };

    return (
        <div className="p-6 space-y-6">
            <h1 className="text-2xl font-bold">Búsqueda de Material</h1>

            <div className="flex justify-center">
                <Card className="w-full max-w-2xl">
                    <CardContent className="p-6">
                        <form onSubmit={handleSearch} className="flex gap-2">
                            <div className="relative flex-1">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                                <Input
                                    placeholder="Buscar documentos, libros, recursos..."
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    className="pl-10"
                                />
                            </div>
                            <Button type="submit">
                                Buscar
                            </Button>
                        </form>
                    </CardContent>
                </Card>
            </div>

            <div className="text-center py-12 text-gray-500">
                <Search className="h-12 w-12 mx-auto mb-4 opacity-20" />
                <p>Ingresa un término para comenzar la búsqueda</p>
            </div>
        </div>
    );
}
