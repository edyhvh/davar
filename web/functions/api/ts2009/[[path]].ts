type Ts2009BucketObject = {
	body: ReadableStream<Uint8Array> | null;
	httpEtag?: string;
};

type Ts2009Context = {
	request: Request;
	params: { path?: string | string[] };
	env: {
		TS2009_BUCKET: {
			get: (key: string) => Promise<Ts2009BucketObject | null>;
		};
	};
};

const buildJsonHeaders = (etag?: string): Headers => {
	const headers = new Headers({
		"Cache-Control": "public, max-age=300, s-maxage=3600",
		"Content-Type": "application/json; charset=utf-8",
		"X-Content-Type-Options": "nosniff",
	});

	if (etag) {
		headers.set("ETag", etag);
	}

	return headers;
};

const normalizeObjectKey = (
	pathValue: string | string[] | undefined,
): string | null => {
	const rawSegments = Array.isArray(pathValue)
		? pathValue
		: typeof pathValue === "string" && pathValue.length > 0
			? pathValue.split("/")
			: [];
	const segments = rawSegments
		.flatMap((segment) => segment.split("/"))
		.map((segment) => segment.trim())
		.filter(Boolean);

	if (segments.length === 0) {
		return null;
	}

	if (segments.some((segment) => segment === "." || segment === "..")) {
		return null;
	}

	return segments.join("/");
};

const handleGet = async (context: Ts2009Context): Promise<Response> => {
	const objectKey = normalizeObjectKey(context.params.path);
	if (!objectKey) {
		return new Response("Not Found", { status: 404 });
	}

	const bucket = context.env?.TS2009_BUCKET;
	if (!bucket || typeof bucket.get !== "function") {
		return new Response("TS2009 bucket binding is not configured", {
			status: 503,
		});
	}

	let object: Ts2009BucketObject | null;
	try {
		object = await bucket.get(objectKey);
	} catch {
		return new Response("TS2009 bucket read failed", { status: 503 });
	}

	if (!object?.body) {
		return new Response("Not Found", { status: 404 });
	}

	const ifNoneMatch = context.request.headers.get("if-none-match");
	if (ifNoneMatch && object.httpEtag && ifNoneMatch === object.httpEtag) {
		return new Response(null, {
			status: 304,
			headers: buildJsonHeaders(object.httpEtag),
		});
	}

	return new Response(object.body, {
		status: 200,
		headers: buildJsonHeaders(object.httpEtag),
	});
};

export const onRequest = async (context: Ts2009Context): Promise<Response> => {
	if (context.request.method !== "GET" && context.request.method !== "HEAD") {
		return new Response("Method Not Allowed", {
			status: 405,
			headers: { Allow: "GET, HEAD" },
		});
	}

	const response = await handleGet(context);
	if (context.request.method === "HEAD") {
		return new Response(null, {
			status: response.status,
			headers: response.headers,
		});
	}

	return response;
};