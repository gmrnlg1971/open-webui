<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import { getWebhookDeliveries } from '$lib/apis';
	import dayjs from 'dayjs';

	const i18n = getContext('i18n');

	export let show = false;

	let deliveries = [];
	let loading = false;

	const loadDeliveries = async () => {
		loading = true;
		try {
			deliveries = await getWebhookDeliveries(localStorage.token);
		} catch (error) {
			console.error(error);
		}
		loading = false;
	};

	$: if (show) {
		loadDeliveries();
	}
</script>

<Modal size="lg" bind:show>
	<div>
		<div class=" flex justify-between dark:text-gray-300 px-5 pt-4 pb-2">
			<div class=" text-lg font-medium capitalize">
				{$i18n.t('Webhook Deliveries')}
			</div>
			<button
				class="rounded-full flex items-center justify-center bg-white text-gray-900 transition hover:bg-gray-200"
				on:click={() => {
					show = false;
				}}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 20 20"
					fill="currentColor"
					class="w-5 h-5"
				>
					<path
						fill-rule="evenodd"
						d="M5.22 5.22a.75.75 0 0 1 1.06 0L10 8.94l3.72-3.72a.75.75 0 1 1 1.06 1.06L11.06 10l3.72 3.72a.75.75 0 1 1-1.06 1.06L10 11.06l-3.72 3.72a.75.75 0 0 1-1.06-1.06L8.94 10 5.22 6.28a.75.75 0 0 1 0-1.06Z"
						clip-rule="evenodd"
					/>
				</svg>
			</button>
		</div>

		<div class="flex flex-col md:flex-row w-full px-5 pb-4 md:space-x-4 dark:text-gray-200">
			<div class=" flex flex-col w-full sm:flex-row sm:justify-center sm:space-x-6">
				{#if loading}
					<div class="text-center">{$i18n.t('Loading...')}</div>
				{:else if deliveries.length === 0}
					<div class="text-center text-gray-500">{$i18n.t('No webhook deliveries found.')}</div>
				{:else}
					<div class="w-full flex flex-col gap-2 max-h-[500px] overflow-y-auto">
						{#each deliveries as delivery}
							<div class="flex flex-col p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
								<div class="flex justify-between">
									<div class="font-medium text-sm">{delivery.url}</div>
									<div class="text-xs text-gray-500">
										{dayjs(delivery.created_at / 1000000).format('MMM D, YYYY h:mm A')}
									</div>
								</div>
								<div class="flex items-center gap-2 mt-1">
									<span
										class="px-2 py-0.5 text-xs rounded-full font-medium {delivery.status ===
										'success'
											? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-500'
											: delivery.status === 'pending'
												? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-500'
												: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-500'}"
									>
										{delivery.status}
									</span>
									<span class="text-xs text-gray-500">
										{$i18n.t('Retries')}: {delivery.retries}
									</span>
								</div>
								{#if delivery.error}
									<div class="mt-2 text-xs text-red-500 bg-red-50 dark:bg-red-900/20 p-2 rounded">
										{delivery.error}
									</div>
								{/if}
								{#if delivery.message}
									<div class="mt-2 text-xs text-gray-600 dark:text-gray-400">
										{delivery.message}
									</div>
								{/if}
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	</div>
</Modal>
