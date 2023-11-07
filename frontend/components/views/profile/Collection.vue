<template>
  <v-col>Collection</v-col>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import Subjective from '@/mixins/subjective'

@Component
class Collection extends mixins(Subjective) {

}

export default toNative(Collection)
</script>
