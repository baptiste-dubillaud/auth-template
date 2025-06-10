import { NextRequest, NextResponse } from 'next/server';
import { backendRequest } from '@/api/api';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        
        const data = await backendRequest('/auth/standard/register', {
            method: 'POST',
            body: JSON.stringify(body),
        });
        
        return NextResponse.json(data);
    } catch (error) {
        console.error('Registration API error:', error);
        return NextResponse.json(
            { detail: error instanceof Error ? error.message : 'Internal server error' },
            { status: 500 }
        );
    }
}