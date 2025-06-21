import { NextRequest, NextResponse } from 'next/server';
import { backendRequest } from '@/app/api/api';

export async function GET(request: NextRequest) {
    try {
        const token = request.headers.get('Authorization')?.replace('Bearer ', '');
        if (!token) {
            return NextResponse.json({ detail: 'Unauthorized' }, { status: 401 });
        }

        const data = await backendRequest('/auth/standard/me', {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        return NextResponse.json(data);
    } catch (error) {
        console.error('Me API error:', error);
        return NextResponse.json(
            { detail: 'Internal server error' },
            { status: 500 }
        );
    }
}