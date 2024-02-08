<template>
  <div>
    <router-view ref="current"></router-view>
  </div>
</template>

<script lang="ts">

import {ArtVue} from '@/lib/lib.ts'

export default class Routed extends ArtVue {
  // Container for routing tests.
}
</script>
