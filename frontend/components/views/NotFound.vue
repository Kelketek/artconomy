<template>
  <div></div>
</template>

<script setup lang="ts">
import {onMounted} from 'vue'
import {ArtStore} from '@/store'
import {useStore} from 'vuex'

const store = useStore<ArtStore>()

onMounted(() => store.commit('errors/setError', {response: {status: 404}}))
</script>

<style scoped>

</style>
