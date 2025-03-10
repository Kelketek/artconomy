<template>
  <v-container
    fluid
    class="pa-0"
  >
    <v-row
      no-gutters
      :style="{'min-height': minHeight}"
    >
      <v-col
        class="text-center"
        align-self="center"
      >
        <v-progress-circular
          indeterminate
          :size="70"
          :width="7"
          color="purple"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
withDefaults(defineProps<{minHeight?: string}>(), {minHeight: '50vh'})
</script>
