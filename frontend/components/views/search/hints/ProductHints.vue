<template>
  <v-col>
    <v-row no-gutters>
      <v-col class="text-center" cols="12">
        Try terms like:
        <p class="mb-0">
          <v-chip color="secondary" variant="flat" @click="search('refsheet')" class="mx-1">refsheet</v-chip>
          <v-chip color="secondary" variant="flat" @click="search('badge')" class="mx-1">badge</v-chip>
          <v-chip color="secondary" variant="flat" @click="search('stickers')" class="mx-1">stickers</v-chip>
        </p>
      </v-col>
    </v-row>
  </v-col>
</template>

<script setup lang="ts">
import {useForm} from '@/store/forms/hooks.ts'

const searchForm = useForm('search')
const search = (val: string) => searchForm.fields.q.model = val
</script>
